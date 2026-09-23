# Tool behavior pilot: bounded timeout

Consider the true finite statement:

> There is no injective function from a 20-element set to a 19-element set.

For this pilot, encode the negation as a Boolean pigeonhole instance and give Z3 a
deliberately insufficient one-millisecond solver budget. The expected result is
`UNKNOWN`, not a mathematical verdict. A timeout must leave the claim `proposed`.
