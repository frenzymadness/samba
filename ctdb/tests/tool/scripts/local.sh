# Hey Emacs, this is a -*- shell-script -*- !!!  :-)

[ -n "$TEST_VAR_DIR" ] || die "TEST_VAR_DIR unset"

setup_ctdb_base "$TEST_VAR_DIR" "unit_tool" \
		functions

if "$TEST_VERBOSE" ; then
    debug () { echo "$@" ; }
else
    debug () { : ; }
fi

ctdbd_socket="${CTDB_BASE}/ctdbd.socket"
ctdbd_pidfile="${CTDB_BASE}/ctdbd.pid"

define_test ()
{
    _f=$(basename "$0" ".sh")

    case "$_f" in
	ctdb.*)
	    _cmd="${_f#ctdb.}"
	    _cmd="${_cmd%.*}" # Strip test number
	    export CTDB_SOCKET="$ctdbd_socket"
	    export CTDB="ctdb"
	    export CTDB_DEBUGLEVEL=NOTICE
	    if [ -z "$FAKE_CTDBD_DEBUGLEVEL" ] ; then
		    FAKE_CTDBD_DEBUGLEVEL="ERR"
	    fi
	    export FAKE_CTDBD_DEBUGLEVEL
	    test_args="$_cmd"
	    ;;
	*)
	    die "Unknown pattern for testcase \"$_f\""
    esac

    printf "%-28s - %s\n" "$_f" "$1"
}

cleanup_ctdbd ()
{
	debug "Cleaning up fake ctdbd"

	pid=$(cat "$ctdbd_pidfile" 2>/dev/null || echo)
	if [ -n "$pid" ] ; then
		kill $pid || true
		rm -f "$ctdbd_pidfile"
	fi
	rm -f "$ctdbd_socket"
}

setup_ctdbd ()
{
	echo "Setting up fake ctdbd"

	$VALGRIND fake_ctdbd -d "$FAKE_CTDBD_DEBUGLEVEL" \
		  -s "$ctdbd_socket" -p "$ctdbd_pidfile"
	# Wait till fake_ctdbd is running
	wait_until 10 test -S "$ctdbd_socket" || \
		die "fake_ctdbd failed to start"

	test_cleanup cleanup_ctdbd
}

ctdbd_getpid ()
{
	cat "$ctdbd_pidfile"
}

setup_natgw ()
{
	debug "Setting up NAT gateway"

	export CTDB_NATGW_HELPER="${CTDB_SCRIPTS_TOOLS_HELPER_DIR}/ctdb_natgw"
	export CTDB_NATGW_NODES="${CTDB_BASE}/natgw_nodes"

	cat >"$CTDB_NATGW_NODES"
}

setup_lvs ()
{
	debug "Setting up LVS"

	export CTDB_LVS_HELPER="${CTDB_SCRIPTS_TOOLS_HELPER_DIR}/ctdb_lvs"
	export CTDB_LVS_NODES="${CTDB_BASE}/lvs_nodes"

	cat >"$CTDB_LVS_NODES"
}

setup_nodes ()
{
    _pnn="$1"

    _f="${CTDB_BASE}/nodes${_pnn:+.}${_pnn}"

    cat >"$_f"
}

simple_test_other ()
{
	(unit_test $CTDB -d $CTDB_DEBUGLEVEL "$@")
	status=$?
	[ $status -eq 0 ] || exit $status
}

simple_test ()
{
	simple_test_other $test_args "$@"
}
