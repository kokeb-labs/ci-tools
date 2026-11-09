// Compliant: a locale is passed explicitly where one is needed; the global one is left alone.
#ifndef KV_RULE_25_5_1_OK_HPP
#define KV_RULE_25_5_1_OK_HPP

#include <locale>

namespace kv::rule_25_5_1::ok {

[[nodiscard]] inline const std::locale& formatting_locale() { return std::locale::classic(); }

}  // namespace kv::rule_25_5_1::ok

#endif  // KV_RULE_25_5_1_OK_HPP
