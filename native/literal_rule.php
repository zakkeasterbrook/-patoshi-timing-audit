<?php
// Independent implementation of the article's three stated criteria.
require 'vendor/autoload.php';
$source = file_get_contents(getenv('PATOSHI_SOURCE'));
if (preg_match('/\$patoshiBlocks = array\(([0-9,]+)\);/', $source, $match) !== 1) {
    throw new RuntimeException('Cannot extract published numeric classification list');
}
$labels = array_fill_keys(array_map('intval', explode(',', $match[1])), true);
$rows = json_decode(file_get_contents(getenv('PATOSHI_HEADERS')), true, 512, JSON_THROW_ON_ERROR);
$byHeight = [];
foreach ($rows as $row) { $byHeight[$row['height']] = $row; }
ksort($byHeight);
foreach ($byHeight as $height => $row) {
    if ($height < 2 || !isset($byHeight[$height - 2]) || !isset($byHeight[$height - 1])) { continue; }
    if (!isset($labels[$height - 2]) || !isset($labels[$height - 1]) || isset($labels[$height])) { continue; }
    $first = $byHeight[$height - 2]['timestamp'];
    $second = $byHeight[$height - 1]['timestamp'];
    if ($second < $first + 600) {
        $delta = $row['timestamp'] - $second;
        echo "$height,$delta\n";
    }
}
