// Edge cases: a const object made external by an extern declaration, and a non-const static data member, both
// defined in a header (kept apart: the CodeQL query skips const and static variables).
#ifndef KV_RULE_6_2_4_BAD_CONST_STATIC_HPP
#define KV_RULE_6_2_4_BAD_CONST_STATIC_HPP

#include <cstdint>

namespace kv::rule_6_2_4::bad_const_static {

extern std::int32_t const kScale;
std::int32_t const kScale = 4;  // seeded

struct Config {
  static std::int32_t level;
};
std::int32_t Config::level = 1;  // seeded

}  // namespace kv::rule_6_2_4::bad_const_static

#endif  // KV_RULE_6_2_4_BAD_CONST_STATIC_HPP
