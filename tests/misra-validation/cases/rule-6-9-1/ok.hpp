#ifndef KV_RULE_6_9_1_OK_HPP
#define KV_RULE_6_9_1_OK_HPP

// Compliant: every declaration of the function uses the same alias.
#include <cstdint>

namespace kv::rule_6_9_1::ok {

using Millis = std::uint32_t;

Millis elapsed(Millis start);

inline Millis elapsed(Millis start) { return (start < 1000U) ? (start + 1U) : start; }

}  // namespace kv::rule_6_9_1::ok

#endif  // KV_RULE_6_9_1_OK_HPP
