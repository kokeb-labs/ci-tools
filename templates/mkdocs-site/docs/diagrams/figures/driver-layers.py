"""The layers of a Kokeb Labs driver: your application, the hardware-agnostic core, the interface, your port.

Reads: Top to bottom, each arrow is a call. The application calls the driver object. The driver turns each call
into register or command transactions and never touches the hardware itself; it hands them to the communication
interface, the small set of methods it needs (transfer, GPIO, delay). The platform port you write implements them
with the MCU's SDK and drives the chip. Notes on the right say which layers are shared and which one is yours. A
repository replaces this hand-placed figure with one whose data() reads the real class and method names from its
headers.
"""

from kokeb_mkdocs_theme.figkit import Fig


def build(_data):
    f = Fig(
        "driver-layers",
        "The layers, one of them yours",
        alt="Layer diagram: your application calls the hardware-agnostic driver, which sends transactions through "
        "the communication interface to the platform port you write, which drives the chip; only the port changes "
        "from one MCU to the next.",
        width=1200,
        kicker="Architecture",
        subtitle="Each arrow is a call. Only the port changes from one MCU to the next.",
        profile="overview",
        legend=[("teal", "you write"), ("brand", "this library"), ("slate", "hardware"), ("~solid", "calls")],
    )
    W = f.body_w
    side, gap, row = 300, 40, 64
    M = W - side - gap
    nx = M + gap
    app = f.card(0, 0, M, "Your application", ["control loop, state machine, CLI"], tone="teal", accent=True)
    core = f.card(0, app.b + row, M, "Hardware-agnostic core", ["Driver<Comm>: configure, read, write, errors"],
                  tone="brand", accent=True)
    comm = f.card(0, core.b + row, M, "Communication interface", ["transfer(), gpioSet(), delayUs()"],
                  tone="brand", accent=True, mono=True)
    port = f.card(0, comm.b + row, M, "Your port", ["ESP-IDF, STM32 HAL, Zephyr, Linux"], tone="teal", accent=True)
    chip = f.card(0, port.b + row, M, "The chip", ["SPI, I2C or UART, and control pins"], tone="slate", accent=True)
    for a, b, verb in ((app, core, "calls"), (core, comm, "register reads and writes"),
                       (comm, port, "forwards to your hooks"), (port, chip, "bus transfers")):
        f.edge([(M / 2, a.b + 4), (M / 2, b.y - 4)], label=verb)
    f.note(nx, core.y, side, "The core and the interface are the same code on every MCU and on the host.",
           tone="brand", title="Shared")
    f.note(nx, port.y, side, "One small class per MCU or board.", tone="teal", title="Yours")
    return f
