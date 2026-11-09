// Edge case (lambda): the result of a lambda call dropped.
#include <cstdint>

namespace kv::rule_0_1_2::bad_lambda {

void call_lambda(std::uint32_t v) {
  const auto twice = [](std::uint32_t x) { return x << 1U; };
  twice(v);  // lambda result dropped  // seeded
}

}  // namespace kv::rule_0_1_2::bad_lambda
