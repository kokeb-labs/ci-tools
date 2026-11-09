// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_13_4_OK_NEAR_HPP
#define KV_RULE_5_13_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_13_4::near {

// A hex literal that fits int is signed: no U is due. The unsigned one carries it.
inline std::int32_t max_signed() { return 0x7FFFFFFF; }
inline std::uint32_t all_ones() { return 0xFFFF'FFFFU; }

}  // namespace kv::rule_5_13_4::near

#endif  // KV_RULE_5_13_4_OK_NEAR_HPP
