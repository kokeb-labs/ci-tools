// Near miss: a parameter used only plainly may be given another macro.
#ifndef KV_RULE_19_3_3_OK_PLAIN_HPP
#define KV_RULE_19_3_3_OK_PLAIN_HPP

#include <cstdint>

#define KV_RULE_19_3_3_LIMIT 7U
#define KV_RULE_19_3_3_TWICE(X) ((X) * 2U)

namespace kv::rule_19_3_3::ok_plain {

inline std::uint32_t limit() { return KV_RULE_19_3_3_TWICE(KV_RULE_19_3_3_LIMIT); }

}  // namespace kv::rule_19_3_3::ok_plain

#undef KV_RULE_19_3_3_TWICE
#undef KV_RULE_19_3_3_LIMIT

#endif  // KV_RULE_19_3_3_OK_PLAIN_HPP
