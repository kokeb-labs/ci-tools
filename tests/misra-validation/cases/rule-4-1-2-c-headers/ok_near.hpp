// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_C_HEADERS_OK_NEAR_HPP
#define KV_RULE_4_1_2_C_HEADERS_OK_NEAR_HPP

#include <climits>
#include <cstddef>
#include <cstdint>

namespace kv::rule_4_1_2_c_headers::near {

// C compatibility headers that are not deprecated.
inline std::size_t bits_of_word() { return sizeof(std::uint32_t) * static_cast<std::size_t>(CHAR_BIT); }

}  // namespace kv::rule_4_1_2_c_headers::near

#endif  // KV_RULE_4_1_2_C_HEADERS_OK_NEAR_HPP
