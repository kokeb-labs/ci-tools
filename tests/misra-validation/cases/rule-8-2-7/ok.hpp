// Compliant: the code compares pointers, it never turns them into integers.
#ifndef KV_RULE_8_2_7_OK_HPP
#define KV_RULE_8_2_7_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_7::ok {

inline bool same_word(const std::uint32_t* a, const std::uint32_t* b) { return a == b; }

}  // namespace kv::rule_8_2_7::ok

#endif  // KV_RULE_8_2_7_OK_HPP
