<?php
// Deterministic offline adapter for the three RPC/response operations used
// by the audited script. It performs no network operations.
namespace Denpa\Bitcoin;
class OfflineDataMissing extends \RuntimeException {}
final class OfflineResponse {
    private array $data;
    public function __construct(array $data) { $this->data = $data; }
    public function get(string $key) {
        if (!array_key_exists($key, $this->data)) {
            throw new \RuntimeException("Unsupported response key: " . $key);
        }
        return $this->data[$key];
    }
}
final class Client {
    private array $byHeight = [];
    private array $byHash = [];
    public function __construct(string $unusedUrl) {
        $filename = getenv('PATOSHI_HEADERS');
        if ($filename === false || $filename === '') {
            throw new \RuntimeException('PATOSHI_HEADERS not set');
        }
        $rows = json_decode(file_get_contents($filename), true, 512, JSON_THROW_ON_ERROR);
        foreach ($rows as $row) {
            $height = $row['height'];
            $hash = $row['block_hash'];
            $time = $row['timestamp'];
            if (!is_int($height) || !is_int($time) || !is_string($hash) || strlen($hash) !== 64) {
                throw new \RuntimeException('Invalid header-data row');
            }
            if (isset($this->byHeight[$height]) || isset($this->byHash[$hash])) {
                throw new \RuntimeException('Duplicate height/hash');
            }
            $this->byHeight[$height] = $hash;
            $this->byHash[$hash] = ['time' => $time, 'height' => $height, 'hash' => $hash];
        }
    }
    public function getBlockHash(int $height): string {
        if (!isset($this->byHeight[$height])) {
            throw new OfflineDataMissing('Missing height: ' . $height);
        }
        return $this->byHeight[$height];
    }
    public function getBlock(string $hash): OfflineResponse {
        if (!isset($this->byHash[$hash])) {
            throw new OfflineDataMissing('Missing hash: ' . $hash);
        }
        return new OfflineResponse($this->byHash[$hash]);
    }
}
