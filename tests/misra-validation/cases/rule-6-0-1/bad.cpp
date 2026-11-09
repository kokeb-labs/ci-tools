// Seeded violation: a function declared inside a block, which reads like a variable definition.
#include <cstdint>

namespace kv::rule_6_0_1::bad {

struct Counter {
  std::int32_t start{0};
};

std::int32_t first() {
  Counter counter();  // declares a function, not an object
  std::int32_t helper(std::int32_t);
  return 0;
}

}  // namespace kv::rule_6_0_1::bad
