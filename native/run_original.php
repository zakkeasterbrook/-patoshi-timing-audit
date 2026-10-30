<?php
// The source is required unchanged; only its RPC dependency is substituted.
// Exit3 explicitly marks a partial run if a finite header prefix is supplied.
$source = getenv('PATOSHI_SOURCE');
if ($source === false || $source === '') { throw new RuntimeException('PATOSHI_SOURCE not set'); }
try { require $source; }
catch (\Denpa\Bitcoin\OfflineDataMissing $error) {
    fwrite(STDERR, "PARTIAL_DATA: " . $error->getMessage() . "\n");
    exit(3);
}
