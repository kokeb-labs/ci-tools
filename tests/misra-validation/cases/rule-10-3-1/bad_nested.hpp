// Seeded violation (nested): an anonymous namespace nested in a named one, in a header.
#ifndef KV_RULE_10_3_1_BAD_NESTED_HPP
#define KV_RULE_10_3_1_BAD_NESTED_HPP

#include <cstdint>

namespace kv::rule_10_3_1::bad_nested {

namespace {  // seeded

inline std::uint32_t twice(std::uint32_t v) { return v << 1U; }

}  // namespace

inline std::uint32_t quad(std::uint32_t v) { return twice(twice(v)); }

}  // namespace kv::rule_10_3_1::bad_nested

#endif  // KV_RULE_10_3_1_BAD_NESTED_HPP
