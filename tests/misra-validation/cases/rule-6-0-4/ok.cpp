// Compliant: main is the global entry point; other functions have other names.
#include <cstdint>

namespace {

std::int32_t run() { return 0; }

}  // namespace

int main() { return run(); }
