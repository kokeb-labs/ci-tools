#ifndef KV_RULE_7_0_4_OK_HPP
#define KV_RULE_7_0_4_OK_HPP

// Compliant: unsigned operands of the same type and an in-range shift count.
#include <cstdint>

namespace kv::rule_7_0_4::ok {

inline std::uint32_t low_nibble(std::uint32_t v) { return v & 0x0FU; }

inline std::uint32_t shifted(std::uint32_t v) { return v << 2U; }

}  // namespace kv::rule_7_0_4::ok

#endif  // KV_RULE_7_0_4_OK_HPP
