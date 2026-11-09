// Compliant: hexadecimal for the bit pattern; plain 0 is allowed.
#ifndef KV_RULE_5_13_3_OK_HPP
#define KV_RULE_5_13_3_OK_HPP

#include <cstdint>

namespace kv::rule_5_13_3::ok {

inline std::uint32_t mode() { return 0x1EDU; }

inline std::uint32_t zero() { return 0U; }

}  // namespace kv::rule_5_13_3::ok

#endif  // KV_RULE_5_13_3_OK_HPP
