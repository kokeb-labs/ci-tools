// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_2_1::bad_edge {

namespace {
std::uint32_t unused_file_local = 3U;  // internal linkage, never referenced  // seeded
}  // namespace

std::uint32_t in_lambda(std::uint32_t v) {
  const auto f = [](std::uint32_t x) {
    const std::uint32_t spare = 9U;  // never referenced  // seeded
    return x;
  };
  return f(v);
}

}  // namespace kv::rule_0_2_1::bad_edge
