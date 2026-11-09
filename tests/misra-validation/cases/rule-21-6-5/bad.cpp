// Seeded violation: delete through a pointer to a class that is only declared here.
namespace kv::rule_21_6_5::bad {

struct Opaque;

void destroy(Opaque* handle) { delete handle; }  // seeded

}  // namespace kv::rule_21_6_5::bad
