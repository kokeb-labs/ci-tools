#ifndef KV_RULE_6_4_2_USING_OK_HPP
#define KV_RULE_6_4_2_USING_OK_HPP

// Compliant: the using-declaration follows every overload it is meant to bring in.
#include <cstdint>

namespace kv::rule_6_4_2_using::ok {

namespace lib {
inline std::int32_t convert(std::int32_t v) { return v; }
inline std::int32_t convert(std::int64_t v) { return (v > 100) ? 100 : static_cast<std::int32_t>(v); }
}  // namespace lib

using lib::convert;

inline std::int32_t use() {
  std::int64_t const wide = 5;
  return convert(wide);
}

}  // namespace kv::rule_6_4_2_using::ok

#endif  // KV_RULE_6_4_2_USING_OK_HPP
