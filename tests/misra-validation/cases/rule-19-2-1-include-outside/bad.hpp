// Seeded violation: an #include placed before the include guard opens.
#include <cstdint>  // seeded

#ifndef KV_RULE_19_2_1_INCLUDE_OUTSIDE_BAD_HPP
#define KV_RULE_19_2_1_INCLUDE_OUTSIDE_BAD_HPP

namespace kv::rule_19_2_1_include_outside::bad {

inline std::uint8_t one() { return 1U; }

}  // namespace kv::rule_19_2_1_include_outside::bad

#endif  // KV_RULE_19_2_1_INCLUDE_OUTSIDE_BAD_HPP
