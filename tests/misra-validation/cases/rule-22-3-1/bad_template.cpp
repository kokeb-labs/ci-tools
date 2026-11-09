// Seeded violation: assert on a constexpr constant inside a template and inside a lambda.
#include <cassert>
#include <cstdint>

namespace kv::rule_22_3_1::bad_template {

inline constexpr std::int32_t kChannels = 8;

template <typename T>
T clamp_channel(T channel) {
  assert(kChannels > 0);  // seeded
  return (channel < static_cast<T>(kChannels)) ? channel : static_cast<T>(kChannels - 1);
}

std::int32_t pick(std::int32_t channel) {
  const auto check = []() { assert(sizeof(std::uint16_t) == 2U); };  // seeded
  check();
  return clamp_channel(channel);
}

}  // namespace kv::rule_22_3_1::bad_template
