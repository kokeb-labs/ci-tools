// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_1_1::bad_edge {

std::uint32_t overwrite_in_lambda(std::uint32_t a) {
  const auto f = [](std::uint32_t x) {
    std::uint32_t r = x;
    r = 3U;  // the first value is never read
    return r;
  };
  return f(a);
}

std::uint32_t write_then_return_other(std::uint32_t a) {
  std::uint32_t tmp = a ^ 5U;  // never read
  tmp = a;
  return tmp;
}

}  // namespace kv::rule_0_1_1::bad_edge
