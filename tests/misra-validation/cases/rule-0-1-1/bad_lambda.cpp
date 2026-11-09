// Edge case (lambda): a local inside a lambda body overwritten before its first value is read.
#include <cstdint>

namespace kv::rule_0_1_1::bad_lambda {

std::uint32_t overwrite_in_lambda(std::uint32_t a) {
  const auto f = [](std::uint32_t x) {
    std::uint32_t r = x;  // seeded
    r = 3U;  // the first value is never read
    return r;
  };
  return f(a);
}

}  // namespace kv::rule_0_1_1::bad_lambda
