// Near misses (near): parameters that are written, forwarded to a writer, or by value.
#ifndef KV_RULE_10_1_1_OK_NEAR_HPP
#define KV_RULE_10_1_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_1_1::ok_near {

inline void zero_first(std::uint32_t* values) { values[0] = 0U; }

inline void clear(std::uint32_t& v) { v = 0U; }

inline void reset_twice(std::uint32_t& v) {
  clear(v);
  clear(v);
}

inline std::uint32_t add(std::uint32_t a, std::uint32_t b) { return a | b; }

}  // namespace kv::rule_10_1_1::ok_near

#endif  // KV_RULE_10_1_1_OK_NEAR_HPP
