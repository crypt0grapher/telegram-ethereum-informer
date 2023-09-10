def format_message(tx, f):
    filter_name = f.name
    return f"""
    <b>Filter:</b> {filter_name}
    <b>Transaction</b>
    <b>From:</b> {tx["from"]}
    <b>To:</b> {tx["to"]}
    <b>Value:</b> {tx["value"]}
    <b>Block:</b> {tx["blockNumber"]}
    <b>Hash:</b> {tx["hash"]}
    """
