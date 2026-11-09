// Near miss: the guard spelled #if !defined(...).
#if !defined(KV_RULE_19_2_1_NO_GUARD_OK_IFDEFINED_HPP)
#define KV_RULE_19_2_1_NO_GUARD_OK_IFDEFINED_HPP

#include <cstdint>

namespace kv::rule_19_2_1_no_guard::ok_ifdefined {

inline std::uint8_t one() { return 1U; }

}  // namespace kv::rule_19_2_1_no_guard::ok_ifdefined

#endif  // KV_RULE_19_2_1_NO_GUARD_OK_IFDEFINED_HPP
