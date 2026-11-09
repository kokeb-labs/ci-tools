// Compliant: pointers come from objects, and only to void* (which the guideline allows).
#ifndef KV_RULE_8_2_6_OK_HPP
#define KV_RULE_8_2_6_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_6::ok {

inline std::uint32_t first_word(const std::uint32_t* words) { return *words; }

inline void* erase(std::uint32_t* word) { return static_cast<void*>(word); }

}  // namespace kv::rule_8_2_6::ok

#endif  // KV_RULE_8_2_6_OK_HPP
