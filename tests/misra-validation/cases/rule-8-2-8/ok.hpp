// Compliant for this guideline: the integer type is std::uintptr_t.
#ifndef KV_RULE_8_2_8_OK_HPP
#define KV_RULE_8_2_8_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_8::ok {

inline std::uintptr_t address_of(const std::uint32_t* word) { return reinterpret_cast<std::uintptr_t>(word); }

}  // namespace kv::rule_8_2_8::ok

#endif  // KV_RULE_8_2_8_OK_HPP
