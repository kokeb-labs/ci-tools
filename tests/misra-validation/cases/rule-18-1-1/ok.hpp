// Compliant: errors are returned, nothing is thrown.
#ifndef KV_RULE_18_1_1_OK_HPP
#define KV_RULE_18_1_1_OK_HPP

namespace kv::rule_18_1_1::ok {

enum class Status : unsigned char { kOk, kFault };

[[nodiscard]] inline Status fail() { return Status::kFault; }

}  // namespace kv::rule_18_1_1::ok

#endif  // KV_RULE_18_1_1_OK_HPP
