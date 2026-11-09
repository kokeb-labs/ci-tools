// Compliant: no comment opener inside a block comment.
#ifndef KV_RULE_5_7_1_OK_HPP
#define KV_RULE_5_7_1_OK_HPP

#include <cstdint>

namespace kv::rule_5_7_1::ok {

/* A block comment that stays flat. */
inline std::uint32_t one() { return 1U; }

}  // namespace kv::rule_5_7_1::ok

#endif  // KV_RULE_5_7_1_OK_HPP
