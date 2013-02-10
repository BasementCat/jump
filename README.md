# JuMP - a JSON-based messaging and presence protocol

JuMP is a lightweight protocol for the exchange of presence information and messages.

## Protocol

JuMP uses JSON-RPC version 2.0: see http://www.jsonrpc.org/specification for the details.  All params are named.  Ports are 6630 for SSL (default), 6631 unsecured.  JSON objects are delimited with "\r\n\r\n", this sequence cannot appear in a json object ("\n" must be used for line termination).

### Methods

The following methods are defined:

#### identify

**Params**
* "name": Used by the client to identify who they are
* "password": If the name provided by the client is registered, they must provide the correct password to connect

**Response**
* The string "OK" if identification is successful

**Errors**
* 10: The username or password was invalid