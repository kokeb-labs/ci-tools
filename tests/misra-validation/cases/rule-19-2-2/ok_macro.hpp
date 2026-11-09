// Near miss: the macro expands to a quoted name.
#ifndef KV_RULE_19_2_2_OK_MACRO_HPP
#define KV_RULE_19_2_2_OK_MACRO_HPP

#define KV_RULE_19_2_2_HELPER "kv_helper.hpp"
#include KV_RULE_19_2_2_HELPER
#undef KV_RULE_19_2_2_HELPER

#endif  // KV_RULE_19_2_2_OK_MACRO_HPP
