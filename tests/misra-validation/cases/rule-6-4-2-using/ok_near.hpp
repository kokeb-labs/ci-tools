// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_4_2_USING_OK_NEAR_HPP
#define KV_RULE_6_4_2_USING_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_4_2_using::near {

// Every overload is declared before the using-declaration, so it sees them all.
namespace lib {
inline std::int32_t scale(std::int32_t v) { return v; }
inline std::int32_t scale(std::int16_t v) { return static_cast<std::int32_t>(v); }
}  // namespace lib
using lib::scale;
inline std::int32_t use() {
  const std::int16_t three = 3;
  return scale(three);
}

}  // namespace kv::rule_6_4_2_using::near

#endif  // KV_RULE_6_4_2_USING_OK_NEAR_HPP
