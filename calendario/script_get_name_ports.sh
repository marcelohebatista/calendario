docker ps --format "{{.Names}} {{.Ports}}" | awk '{if ($2 != "") print $1, $2}' | sed 's/0.0.0.0://g'
