// Compliant near miss: a named offset constant from the datasheet, and a function named offset_of.
#ifndef KV_RULE_21_2_4_OK_CONSTANT_HPP
#define KV_RULE_21_2_4_OK_CONSTANT_HPP

#include <cstddef>

namespace kv::rule_21_2_4::ok_constant {

inline constexpr std::size_t kPayloadOffset = 4U;  // datasheet: byte 4 of the frame

[[nodiscard]] inline std::size_t offset_of(bool payload) { return payload ? kPayloadOffset : 0U; }

}  // namespace kv::rule_21_2_4::ok_constant

#endif  // KV_RULE_21_2_4_OK_CONSTANT_HPP
