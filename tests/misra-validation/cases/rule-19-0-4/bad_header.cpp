// Seeded violation: #undef of a macro defined in an included header.
#include "kv_macro.hpp"

#undef KV_RULE_19_0_4_FROM_HEADER

namespace kv::rule_19_0_4::bad_header {

constexpr unsigned char kValue = 1U;

}  // namespace kv::rule_19_0_4::bad_header
