// Seeded violation: an explicit specialisation of a function template.
#include <cstdint>

namespace kv::rule_17_8_1::bad {

template <typename T>
T clamp_low(T v) {
  return v;
}

template <>
std::int32_t clamp_low<std::int32_t>(std::int32_t v) {  // seeded
  return (v < 0) ? 0 : v;
}

}  // namespace kv::rule_17_8_1::bad
