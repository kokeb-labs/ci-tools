// Seeded violation: code after the guard closes.  // seeded
#ifndef KV_RULE_19_2_1_NO_GUARD_BAD_PARTIAL_HPP
#define KV_RULE_19_2_1_NO_GUARD_BAD_PARTIAL_HPP

namespace kv::rule_19_2_1_no_guard::bad_partial {

inline unsigned char one() { return 1U; }

}  // namespace kv::rule_19_2_1_no_guard::bad_partial

#endif  // KV_RULE_19_2_1_NO_GUARD_BAD_PARTIAL_HPP

namespace kv::rule_19_2_1_no_guard::bad_partial_tail {

inline unsigned char two() { return 2U; }

}  // namespace kv::rule_19_2_1_no_guard::bad_partial_tail
