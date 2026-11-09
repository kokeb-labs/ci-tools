// Seeded violation: throwing a pointer from new.
namespace kv::rule_18_1_1::bad_new {

struct Fault {};

void fail() { throw new Fault(); }

}  // namespace kv::rule_18_1_1::bad_new
