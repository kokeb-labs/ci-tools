// Compliant: the global allocation functions are left to the implementation.
#ifndef KV_RULE_21_6_4_OK_HPP
#define KV_RULE_21_6_4_OK_HPP

#include <cstdint>

namespace kv::rule_21_6_4::ok {

[[nodiscard]] inline std::uint32_t pool_blocks() { return 8U; }

}  // namespace kv::rule_21_6_4::ok

#endif  // KV_RULE_21_6_4_OK_HPP
