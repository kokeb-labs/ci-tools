// Seeded violation: an #include after the include guard closes.
#ifndef KV_RULE_19_2_1_INCLUDE_OUTSIDE_BAD_AFTER_HPP
#define KV_RULE_19_2_1_INCLUDE_OUTSIDE_BAD_AFTER_HPP

namespace kv::rule_19_2_1_include_outside::bad_after {

inline unsigned char one() { return 1U; }

}  // namespace kv::rule_19_2_1_include_outside::bad_after

#endif  // KV_RULE_19_2_1_INCLUDE_OUTSIDE_BAD_AFTER_HPP

#include <cstdint>  // seeded
