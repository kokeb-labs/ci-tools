// Compliant: the constant expression stays in range.
#ifndef KV_RULE_8_20_1_OK_HPP
#define KV_RULE_8_20_1_OK_HPP

#include <cstdint>

namespace kv::rule_8_20_1::ok {

inline std::uint32_t in_range() { return 0xFFFFFFF0U + 2U; }

}  // namespace kv::rule_8_20_1::ok

#endif  // KV_RULE_8_20_1_OK_HPP
