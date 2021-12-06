// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract JtnToken {

    enum HoldStatusCode {
        Nonexistent,
        Ordered,
        Executed,
        Removed
    }

    struct Hold {
        address origin;
        address target;
        uint256 amount;
        HoldStatusCode status;
    }

    address private _owner;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    mapping(address => mapping(address => uint256)) private _holdAllowances;
    mapping(string => Hold) private _holds;
    mapping(address => uint256) private _heldBalance;
    uint256 private _totalHeldBalance;
    uint256 private _totalSupply;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event HoldCreated(string holdId, address indexed from, address indexed to, uint256 value);
    event HoldExecuted(string holdId, address indexed from, address indexed to, uint256 value);
    event HoldRemoved(string holdId, address indexed from, address indexed to, uint256 value);
    event HoldApproval(address indexed owner, address indexed spender, uint256 value);


    constructor() public {
        _totalSupply = 10000000000000000;
        _owner = msg.sender;
        _balances[_owner] = _totalSupply;
    }

    modifier onlyOwner() {
        require(msg.sender == _owner);
        _;
    }

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function totalSupplyOnHold() public view returns (uint256) {
        return _totalHeldBalance;
    }

    function balanceOnHold(address account) public view returns (uint256) {
        return _heldBalance[account];
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account] - _heldBalance[account];
    }

    function netBalanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    function transfer(address recipient, uint256 amount) public returns (bool) {

        require(recipient != address(0));
        return _transfer(msg.sender, recipient, amount);
    }

    function transferFrom(address sender, address recipient, uint256 amount) public returns (bool) {

        require(sender != address(0));
        require(recipient != address(0));
        require(amount <= _balances[sender] - _heldBalance[sender]);
        require(amount <= _allowances[sender][msg.sender]);
        _transfer(sender, recipient, amount);
        _approve(sender, msg.sender, _allowances[sender][msg.sender] - amount);
        return true;
    }

    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) public returns (bool) {
        return _approve(msg.sender, spender, amount);
    }

    function hold(address to, uint256 amount, string memory holdId) public returns (bool)
    {
        require(to != address(0), "Payee address must not be zero address");
        return _hold(holdId, msg.sender, to, amount);
    }

    function holdFrom(address from, address to, uint256 amount, string memory holdId) public returns (bool)
    {
        require(to != address(0), "Payee address must not be zero address");
        require(from != address(0), "Payer address must not be zero address");
        require(amount <= _holdAllowances[from][msg.sender]);
        _hold(holdId, from, to, amount);
        _holdApprove(from, msg.sender, _holdAllowances[from][msg.sender] - amount);
        return true;
    }

     function holdAllowance(address owner, address spender) public view returns (uint256) {
        return _holdAllowances[owner][spender];
    }

    function holdApprove(address spender, uint256 amount) public returns (bool) {
        return _holdApprove(msg.sender, spender, amount);
    }

    function executeHold(string memory holdId) public returns (bool) {
        return _executeHold(holdId);
    }

    function removeHold(string memory holdId) public onlyOwner returns (bool) {
        return _removeHold(holdId);
    }

    function _transfer(address sender, address recipient, uint256 amount) private returns (bool) {
        require(amount <= _balances[sender] - _heldBalance[sender]);
        _balances[sender] = _balances[sender] - amount;
        _balances[recipient] = _balances[recipient] + amount;
        emit Transfer(sender, recipient, amount);
        return true;
    }

    function _approve(address owner, address spender, uint256 amount) private returns (bool) {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
        return true;
    }

    function _hold(string memory holdId, address from, address to, uint256 amount) private returns (bool)
    {
        Hold storage newHold = _holds[holdId];

        require(amount != 0, "Value must be greater than zero");
        require(newHold.amount == 0, "This holdId already exists");
        require(amount <= _balances[from] - _heldBalance[from], "Amount of the hold can't be greater than the balance of the origin");

        newHold.origin = from;
        newHold.target = to;
        newHold.amount = amount;
        newHold.status = HoldStatusCode.Ordered;

        _heldBalance[from] = _heldBalance[from] + amount;
        _totalHeldBalance = _totalHeldBalance + amount;

        emit HoldCreated(holdId, from, to, amount);

        return true;
    }

    function _executeHold(string memory holdId) private returns (bool) {

        Hold storage executableHold = _holds[holdId];
        require(executableHold.status == HoldStatusCode.Ordered, "A hold can only be executed in status Ordered");
        require(executableHold.origin == msg.sender, "Only the hold creator has allow execute the hold");
        //Check
        _totalHeldBalance = _totalHeldBalance - executableHold.amount;
        _heldBalance[executableHold.origin] = _heldBalance[executableHold.origin] - executableHold.amount;
        executableHold.status = HoldStatusCode.Executed;
        emit HoldExecuted(holdId, executableHold.origin, executableHold.target, executableHold.amount);
        transfer(executableHold.target, executableHold.amount);

        return true;
    }

    function _removeHold(string memory holdId) private onlyOwner returns (bool) {

        Hold storage removedHold = _holds[holdId];
        require(removedHold.status == HoldStatusCode.Ordered, "A hold can only be executed in status Ordered");
        _totalHeldBalance = _totalHeldBalance - removedHold.amount;
        _heldBalance[removedHold.origin] = _heldBalance[removedHold.origin] - removedHold.amount;
        removedHold.status = HoldStatusCode.Removed;
        emit HoldRemoved(holdId, removedHold.origin, removedHold.target, removedHold.amount);
        return true;
    }

    function _holdApprove(address owner, address spender, uint256 amount) private returns (bool) {
        require(owner != address(0), "Approve from the zero address");
        require(spender != address(0), "Approve to the zero address");
        _holdAllowances[owner][spender] = amount;
        emit HoldApproval(owner, spender, amount);
        return true;
    }
}