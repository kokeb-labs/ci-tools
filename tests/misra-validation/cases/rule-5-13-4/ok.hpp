// Compliant: the unsigned literal carries U.
#ifndef KV_RULE_5_13_4_OK_HPP
#define KV_RULE_5_13_4_OK_HPP

#include <cstdint>

namespace kv::rule_5_13_4::ok {

inline std::uint32_t top_bit() { return 0x80000000U; }

}  // namespace kv::rule_5_13_4::ok

#endif  // KV_RULE_5_13_4_OK_HPP
