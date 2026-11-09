#ifndef KV_RULE_6_2_4_BAD_HPP
#define KV_RULE_6_2_4_BAD_HPP

// Seeded violation: a header defines a non-inline function and a non-inline object.
#include <cstdint>

namespace kv::rule_6_2_4::bad {

std::int32_t twice(std::int32_t v) { return v * 2; }

std::int32_t const kOffset = 3;
extern std::int32_t const kScale;
std::int32_t const kScale = 4;

}  // namespace kv::rule_6_2_4::bad

#endif  // KV_RULE_6_2_4_BAD_HPP
