pragma solidity ^0.8.0;

contract ImageStorage {
    struct BlockData {
        uint256 index;
        uint256 timestamp;
        string inputDataHash;
        string previousHash;
        string result;
    }

    BlockData[] public blocks;

    // 이벤트 추가
    event BlockStored(uint256 index, uint256 timestamp, string inputDataHash, string previousHash, string result);

    function storeBlock(
        uint256 index,
        uint256 timestamp,
        string memory inputDataHash,
        string memory previousHash,
        string memory result
    ) public {
        // 블록 저장
        blocks.push(BlockData(index, timestamp, inputDataHash, previousHash, result));
        
        // 블록 저장 이벤트 발생
        emit BlockStored(index, timestamp, inputDataHash, previousHash, result);
    }

    function getBlock(uint256 index) public view returns (BlockData memory) {
        require(index < blocks.length, "Block index out of bounds"); // 인덱스 범위 체크
        return blocks[index];
    }

    function getAllBlocks() public view returns (BlockData[] memory) {
        return blocks;
    }
}
