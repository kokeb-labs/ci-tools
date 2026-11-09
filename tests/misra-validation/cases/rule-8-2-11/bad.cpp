// Seeded violation: an object with a non-trivial copy constructor goes through an ellipsis.
#include <cstdint>

namespace kv::rule_8_2_11::bad {

struct Sample {
  Sample() = default;
  Sample(const Sample& other) : value(other.value) {}
  std::int32_t value{0};
};

std::int32_t first(std::int32_t count, ...);

std::int32_t use() {
  Sample s;
  return first(1, s);
}

}  // namespace kv::rule_8_2_11::bad
