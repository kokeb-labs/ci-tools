// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_2_4_OK_NEAR_HPP
#define KV_RULE_6_2_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_2_4::near {

// A function template, a class template with a full specialisation, and a static constexpr member: all allowed
// in a header.
template <typename T>
T zero() {
  return T{};
}
template <typename T>
struct Traits {
  static constexpr std::int32_t kBits{0};
};
template <>
struct Traits<std::int32_t> {
  static constexpr std::int32_t kBits{32};
};
struct Config {
  static constexpr std::int32_t kLevel{1};
};
// A namespace-scope const object has internal linkage, so the guideline does not apply.
std::int32_t const kOffset = 3;
inline std::int32_t offset_level() { return kOffset + Config::kLevel; }

}  // namespace kv::rule_6_2_4::near

#endif  // KV_RULE_6_2_4_OK_NEAR_HPP
