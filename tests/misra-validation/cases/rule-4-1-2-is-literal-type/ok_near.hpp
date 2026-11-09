// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_IS_LITERAL_TYPE_OK_NEAR_HPP
#define KV_RULE_4_1_2_IS_LITERAL_TYPE_OK_NEAR_HPP

#include <cstdint>
#include <type_traits>

namespace kv::rule_4_1_2_is_literal_type::near {

// The replacement traits: trivially copyable and standard layout say what the old trait was used for.
template <typename T>
constexpr bool plain_v = std::is_trivially_copyable_v<T> && std::is_standard_layout_v<T>;
inline bool plain() { return plain_v<std::uint32_t>; }

}  // namespace kv::rule_4_1_2_is_literal_type::near

#endif  // KV_RULE_4_1_2_IS_LITERAL_TYPE_OK_NEAR_HPP
