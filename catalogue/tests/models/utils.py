def new(Model, **kwargs):
    return Model.objects.get_or_create(**kwargs)[0]
