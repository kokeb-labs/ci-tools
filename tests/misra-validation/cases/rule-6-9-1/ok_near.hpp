// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_9_1_OK_NEAR_HPP
#define KV_RULE_6_9_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_9_1::near {

// Two aliases, each used consistently in every declaration of its entity.
using Ticks = std::uint32_t;
using Count = std::uint16_t;
Ticks since(Ticks start);
inline Ticks since(Ticks start) { return start; }
Count items(Count n);
inline Count items(Count n) { return n; }

}  // namespace kv::rule_6_9_1::near

#endif  // KV_RULE_6_9_1_OK_NEAR_HPP
